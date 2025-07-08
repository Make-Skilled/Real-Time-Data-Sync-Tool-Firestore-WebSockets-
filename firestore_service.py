import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

class FirestoreService:
    def __init__(self):
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            # For local development, use service account key
            # In production, use environment variables or other secure methods
            try:
                # Try to load from service account file
                cred = credentials.Certificate('./serviceAccountKey.json')
                firebase_admin.initialize_app(cred)
            except FileNotFoundError:
                # Fallback to default credentials (for deployment)
                firebase_admin.initialize_app()
        
        self.db = firestore.client()
    
    def create_poll(self, poll_id, poll_data):
        """Create a new poll in Firestore"""
        try:
            doc_ref = self.db.collection('polls').document(poll_id)
            doc_ref.set(poll_data)
            return True
        except Exception as e:
            print(f"Error creating poll: {e}")
            return False
    
    def get_poll(self, poll_id):
        """Get poll data from Firestore"""
        try:
            doc_ref = self.db.collection('polls').document(poll_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting poll: {e}")
            return None
    
    def cast_vote(self, poll_id, selected_option, user_id):
        """Cast a vote for a specific option"""
        try:
            # Use a transaction to ensure atomic updates
            transaction = self.db.transaction()
            
            @firestore.transactional
            def update_vote(transaction, poll_ref, votes_ref):
                # Get current poll data
                poll_doc = poll_ref.get(transaction=transaction)
                if not poll_doc.exists:
                    return False
                
                poll_data = poll_doc.to_dict()
                
                # Check if option exists
                if selected_option not in poll_data['votes']:
                    return False
                
                # Update vote count
                poll_data['votes'][selected_option] += 1
                
                # Update poll document
                transaction.update(poll_ref, {
                    'votes': poll_data['votes'],
                    'updated_at': datetime.now().isoformat()
                })
                
                # Record user vote to prevent double voting
                transaction.set(votes_ref, {
                    'user_id': user_id,
                    'poll_id': poll_id,
                    'option': selected_option,
                    'timestamp': datetime.now().isoformat()
                })
                
                return True
            
            poll_ref = self.db.collection('polls').document(poll_id)
            votes_ref = self.db.collection('votes').document(f"{poll_id}_{user_id}")
            
            return update_vote(transaction, poll_ref, votes_ref)
            
        except Exception as e:
            print(f"Error casting vote: {e}")
            return False
    
    def has_user_voted(self, poll_id, user_id):
        """Check if user has already voted in this poll"""
        try:
            doc_ref = self.db.collection('votes').document(f"{poll_id}_{user_id}")
            doc = doc_ref.get()
            return doc.exists
        except Exception as e:
            print(f"Error checking vote status: {e}")
            return False
    
    def get_all_polls(self):
        """Get all polls (for admin/debugging)"""
        try:
            polls = []
            docs = self.db.collection('polls').stream()
            for doc in docs:
                poll_data = doc.to_dict()
                poll_data['id'] = doc.id
                polls.append(poll_data)
            return polls
        except Exception as e:
            print(f"Error getting all polls: {e}")
            return []
    
    def delete_poll(self, poll_id):
        """Delete a poll and all associated votes"""
        try:
            # Delete poll document
            self.db.collection('polls').document(poll_id).delete()
            
            # Delete all votes for this poll
            votes_query = self.db.collection('votes').where('poll_id', '==', poll_id)
            votes = votes_query.stream()
            
            for vote in votes:
                vote.reference.delete()
            
            return True
        except Exception as e:
            print(f"Error deleting poll: {e}")
            return False

    def create_user(self, user_id, user_data):
        """Create a new user in Firestore"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.set(user_data)
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False

    def get_user_by_email(self, email):
        """Get a user by email from Firestore"""
        try:
            users_ref = self.db.collection('users')
            query = users_ref.where('email', '==', email).limit(1).stream()
            for doc in query:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None

    def update_poll_status(self, poll_id, active):
        """Update the active status of a poll"""
        try:
            poll_ref = self.db.collection('polls').document(poll_id)
            poll_ref.update({'active': active})
            return True
        except Exception as e:
            print(f"Error updating poll status: {e}")
            return False

    def get_user_votes(self, user_id):
        """Get all votes cast by a user"""
        try:
            votes_query = self.db.collection('votes').where('user_id', '==', user_id).stream()
            votes = []
            for doc in votes_query:
                votes.append(doc.to_dict())
            return votes
        except Exception as e:
            print(f"Error getting user votes: {e}")
            return []
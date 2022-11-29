from django.contrib.auth.tokens import PasswordResetTokenGenerator 
from six import text_type

#token pour le lien de confirmation

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return(
            text_type(user.pk) + text_type(timestamp) #chaque utilisateur a son propre token 
        )
        
generatorToken = TokenGenerator()
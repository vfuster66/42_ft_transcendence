
# users/models.py

#########################################################################################################

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext as _

#########################################################################################################

class Game(models.Model):
    GAME_TYPES = [
        ('pong2d', 'Pong 2D'),
        ('pongapi2d', 'Pong API 2D'),
        ('invaders', 'Invaders'),
    ]
    
    player1 = models.ForeignKey(User, related_name='games_as_player1', on_delete=models.CASCADE, null=True, blank=True)
    player2 = models.ForeignKey(User, related_name='games_as_player2', on_delete=models.CASCADE)
    winner = models.ForeignKey(User, related_name='won_games', on_delete=models.SET_NULL, null=True, blank=True)
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    won = models.BooleanField(default=False)
    game_date = models.DateTimeField(auto_now_add=True)
    is_vs_ai = models.BooleanField(default=False)
    details = models.TextField(blank=True, null=True)
    game_type = models.CharField(max_length=50, choices=GAME_TYPES, default='pong2d')
    tournament = models.ForeignKey('tournaments.Tournament', related_name='games', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.player1} vs {self.player2} - {self.game_type}'

#########################################################################################################

class UserProfile(models.Model):
    # Profil
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    display_name = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        _('status'),
        max_length=10,
        choices=[
            ('ONLINE', _('Online')),
            ('OFFLINE', _('Offline')),
            ('IN_GAME', _('In Game'))
        ],
        default='OFFLINE'
    )
    # Champs pour prénom, nom et leur visibilité
    first_name = models.CharField(_('First name'), max_length=30, null=True, blank=True)
    last_name = models.CharField(_('Last name'), max_length=30, null=True, blank=True)
    location = models.CharField(_('Location'), max_length=100, null=True, blank=True)
    first_name_visible = models.BooleanField(default=True)
    last_name_visible = models.BooleanField(default=True)
    # Pour les statistiques de base
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)
    # Relation d'amis
    friends = models.ManyToManyField("self", blank=True)
    # 2FA
    two_factor_enabled = models.BooleanField(default=False)
    # chat
    blocked_users = models.ManyToManyField('self', symmetrical=False, related_name='blocked_by', blank=True)
    is_blocked = models.BooleanField(default=False)

    def is_blocked_by(self, other_user):
        # Vérifie si other_user est une instance de modèle User
        if not isinstance(other_user, User):
            return False
        
        # Continue avec la logique de vérification des utilisateurs bloqués
        return self.blocked_users.filter(user=other_user).exists()

    def block_user(self, user_profile):
        self.blocked_users.add(user_profile)

    def unblock_user(self, user_profile):
        self.blocked_users.remove(user_profile)

    def win_loss_ratio(self):
        total_games = self.total_wins + self.total_losses
        return self.total_wins / total_games if total_games > 0 else 0
    
    def recent_games(self):
        return self.user.games.order_by('-created_at')[:10]

#########################################################################################################


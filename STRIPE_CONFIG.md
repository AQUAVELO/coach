# 🔑 Configuration Stripe pour AquaCoach

## Étape 1 : Créer un compte Stripe (GRATUIT)

1. Allez sur **https://dashboard.stripe.com/register**
2. Créez votre compte gratuitement
3. Vérifiez votre email

## Étape 2 : Obtenir vos clés API

### En mode TEST (pour développement)

1. Connectez-vous à https://dashboard.stripe.com
2. Assurez-vous d'être en **mode Test** (interrupteur en haut à droite)
3. Allez dans **Développeurs > Clés API**
4. Vous verrez :
   - **Clé publiable** : commence par `pk_test_...`
   - **Clé secrète** : commence par `sk_test_...` (cliquez sur "Révéler la clé")

### Copier les clés dans votre code

Ouvrez `/Applications/MAMP/htdocs/natation/app.py` et remplacez :

```python
# Configuration Stripe
stripe.api_key = "sk_test_VOTRE_CLE_SECRETE_ICI"  # ← Remplacez
STRIPE_PUBLIC_KEY = "pk_test_VOTRE_CLE_PUBLIQUE_ICI"  # ← Remplacez
```

## Étape 3 : Tester avec des cartes de test

En mode TEST, utilisez ces numéros de carte :

### ✅ Paiement réussi
- **Numéro** : `4242 4242 4242 4242`
- **Date** : N'importe quelle date future (ex: 12/25)
- **CVC** : N'importe quel 3 chiffres (ex: 123)
- **Code postal** : N'importe lequel (ex: 75001)

### ❌ Paiement refusé
- **Numéro** : `4000 0000 0000 0002`
- Date/CVC : Idem ci-dessus

### 🔐 3D Secure (authentification requise)
- **Numéro** : `4000 0027 6000 3184`
- Date/CVC : Idem ci-dessus

## Étape 4 : Passer en PRODUCTION

⚠️ **NE PAS faire avant d'avoir testé complètement !**

1. Dans le dashboard Stripe, désactivez le **mode Test**
2. Activez votre compte (vérification d'identité requise)
3. Récupérez vos clés de PRODUCTION :
   - `pk_live_...` (clé publique)
   - `sk_live_...` (clé secrète)
4. Remplacez dans `app.py`

## 💰 Tarifs Stripe

- **Pas d'abonnement** : Gratuit à installer
- **Par transaction** : 1,5% + 0,25€
- **Exemple pour 2€** : vous recevez 1,72€

## 🆘 Support

- Documentation : https://stripe.com/docs
- Support : https://support.stripe.com

## 🔒 Sécurité

- ✅ Les cartes ne transitent JAMAIS par votre serveur
- ✅ Stripe est certifié PCI-DSS Level 1
- ✅ Données chiffrées de bout en bout
- ✅ 3D Secure 2 automatique pour l'Europe


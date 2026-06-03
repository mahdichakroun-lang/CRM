# CRM Mobile - React Native / Expo

Application mobile compagnon du CRM Internal.

## Fonctionnalites

- Login avec les memes identifiants que le CRM web
- Profil utilisateur (lecture + modification nom/telephone)
- Deconnexion securisee (expo-secure-store)
- UI mobile premium (dark/light, gradients, animations)

## Prerequis

1. Node.js (v18+)
2. Expo Go sur mobile
3. Backend CRM en cours d'execution (`docker-compose up -d`)

## Installation

```bash
cd mobile
npm install
```

## Configuration

### URL backend

Par defaut, l'application detecte automatiquement l'hote Expo et utilise:

`http://<host_expo>:8000/api/v1`

Pour forcer une URL specifique, utilisez:

```bash
EXPO_PUBLIC_API_BASE_URL=http://192.168.1.XXX:8000/api/v1
```

Exemple de lancement:

```bash
EXPO_PUBLIC_API_BASE_URL=http://192.168.1.22:8000/api/v1 npx expo start --lan --port 8082
```

### Verification backend

```bash
curl http://192.168.1.XXX:8000/health
```

## Lancement

```bash
npx expo start
```

Puis scanner le QR code avec Expo Go.

## Comptes de demonstration

| Role       | Email              | Mot de passe |
|------------|--------------------|--------------|
| Admin      | admin@crm.com      | admin123     |
| Manager    | fatima@crm.com     | fatima123    |
| Commercial | ahmed@crm.com      | ahmed123     |
| Support    | omar@crm.com       | omar1234     |
| Client     | karim@sonatrach.dz | client123    |

## Structure

```text
mobile/
|- App.js
|- app.json
|- package.json
|- babel.config.js
|- src/
|  |- context/
|  |  |- AuthContext.js
|  |  |- ThemeContext.js
|  |- navigation/
|  |  |- AppNavigator.js
|  |- screens/
|  |  |- LoginScreen.js
|  |  |- ProfileScreen.js
|  |  |- ClientDashboardScreen.js
|  |  |- ClientTicketsScreen.js
|  |  |- ClientQuotesScreen.js
|  |- services/
|  |  |- api.js
|  |- theme/
|     |- colors.js
|- assets/
```
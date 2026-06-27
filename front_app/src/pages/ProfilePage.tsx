import { useAuth } from '../contexts/AuthContext';

const ProfilePage = () => {
  const { user } = useAuth();

  if (!user) {
    return <div className="text-center py-20">Veuillez vous connecter</div>;
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <h1 className="text-3xl font-bold text-primary-800">⚙️ Mon profil</h1>

      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="text-center mb-8">
          <div className="w-24 h-24 bg-gradient-to-r from-primary-500 to-purple-500 rounded-full flex items-center justify-center text-4xl text-white mx-auto mb-4">
            {user.prenom?.[0]}{user.nom?.[0]}
          </div>
          <h2 className="text-2xl font-bold">{user.prenom} {user.nom}</h2>
          <p className="text-gray-600">{user.email}</p>
        </div>

        <div className="space-y-6">
          <div className="border-b pb-4">
            <h3 className="font-semibold text-gray-700 mb-2">Informations personnelles</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Prénom</p>
                <p className="font-medium">{user.prenom}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Nom</p>
                <p className="font-medium">{user.nom}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p className="font-medium">{user.email}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Type d'apprenant</p>
                <p className="font-medium">
                  {user.type_apprenant === 'visuel' && '👁️ Visuel'}
                  {user.type_apprenant === 'auditif' && '👂 Auditif'}
                  {user.type_apprenant === 'lecture' && '📖 Lecture'}
                  {!user.type_apprenant && 'À déterminer'}
                </p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-gray-700 mb-2">Préférences d'apprentissage</h3>
            <div className="flex gap-4">
              <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">📖 Mode Texte</span>
              <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">🎧 Mode Audio</span>
              <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm">🎬 Mode Vidéo</span>
            </div>
          </div>

          <div className="pt-4">
            <button className="w-full px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600">
              ✏️ Modifier le profil
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;


import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';


const Header = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [headerMenuOpen, setHeaderMenuOpen] = useState(false);

  const handleLogout = () => {
    setHeaderMenuOpen(false);
    logout();
    navigate('/login');
  };

  
  const toggleHeaderMenu = () => {
    setHeaderMenuOpen(prev => !prev);
  };

  const closeHeaderMenu = () => {
    setHeaderMenuOpen(false);
  };

  return (
    <header className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          <Link to="/" className="flex items-center gap-2 shrink-0" onClick={closeHeaderMenu}>
            <div className="flex items-center -space-x-2">
              <img
                src="https://img.icons8.com/color/96/000000/html-5--v1.png"
                alt="HTML5"
                className="w-8 h-8 sm:w-9 sm:h-9 rounded"
              />
              <img
                src="https://img.icons8.com/color/96/000000/css3.png"
                alt="CSS3"
                className="w-8 h-8 sm:w-9 sm:h-9 rounded"
              />
              <img
                src="https://img.icons8.com/color/96/000000/javascript--v1.png"
                alt="JavaScript"
                className="w-8 h-8 sm:w-9 sm:h-9 rounded"
              />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-base lg:text-lg font-bold text-primary-800 leading-tight">
                Plateforme Éducative
              </h1>
              <p className="text-[11px] text-gray-500 leading-tight">
                HTML, CSS, JS intelligents
              </p>
            </div>
          </Link>

          
          <div className="hidden lg:flex items-center gap-3">
            {isAuthenticated && (
              <Link
                to="/level-test"
                className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition flex items-center gap-1.5 text-sm font-medium"
              >
                <span>📋</span>
                <span>Tester mon niveau</span>
              </Link>
            )}

            {isAuthenticated && user ? (
              <div className="flex items-center gap-3">
                <span className="text-sm text-gray-700 font-medium">
                  👤 {user.prenom} {user.nom}
                </span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition text-sm font-medium"
                >
                  🚪 Déconnexion
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition text-sm font-medium"
                >
                  🔐 Connexion
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition text-sm font-medium"
                >
                  📝 Inscription
                </Link>
              </div>
            )}
          </div>

          
          <button
            onClick={toggleHeaderMenu}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition relative"
            aria-label="Menu Header"
          >
            {headerMenuOpen ? (
              <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>
      </div>

      
      {headerMenuOpen && (
        <>
          <div
            className="lg:hidden fixed inset-0 bg-black/30 z-40"
            onClick={closeHeaderMenu}
          />
          <div className="lg:hidden fixed top-16 right-0 bottom-0 w-72 bg-white shadow-xl z-50 border-l border-gray-100 overflow-y-auto">
            <div className="p-5 space-y-4">
              
              {isAuthenticated && user && (
                <div className="p-4 bg-gray-50 rounded-xl">
                  <p className="text-sm font-semibold text-gray-800">
                    👤 {user.prenom} {user.nom}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">{user.email}</p>
                </div>
              )}

              
              <nav className="space-y-1">
                <p className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold px-2 mb-1">
                  Navigation
                </p>
                
                <Link
                  to="/courses"
                  onClick={closeHeaderMenu}
                  className="flex items-center gap-3 px-4 py-2.5 rounded-xl text-gray-600 text-sm hover:bg-gray-50 transition-colors"
                >
                  📚 Catalogue des cours
                </Link>
                
                <Link
                  to="/learning/text"
                  onClick={closeHeaderMenu}
                  className="flex items-center gap-3 px-4 py-2.5 rounded-xl text-gray-600 text-sm hover:bg-gray-50 transition-colors"
                >
                  📖 Apprentissage Texte
                </Link>
                
                <Link
                  to="/learning/audio"
                  onClick={closeHeaderMenu}
                  className="flex items-center gap-3 px-4 py-2.5 rounded-xl text-gray-600 text-sm hover:bg-gray-50 transition-colors"
                >
                  🎧 Apprentissage Audio
                </Link>
                
                <Link
                  to="/learning/video"
                  onClick={closeHeaderMenu}
                  className="flex items-center gap-3 px-4 py-2.5 rounded-xl text-gray-600 text-sm hover:bg-gray-50 transition-colors"
                >
                  🎬 Apprentissage Vidéo
                </Link>
              </nav>

              
              <div className="pt-4 border-t border-gray-100 space-y-2">
                <p className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold px-2 mb-1">
                  Mon compte
                </p>
                
                {isAuthenticated ? (
                  <>
                    <Link
                      to="/profile"
                      onClick={closeHeaderMenu}
                      className="flex items-center gap-3 px-4 py-2.5 rounded-xl text-gray-600 text-sm hover:bg-gray-50 transition-colors"
                    >
                      ⚙️ Mon profil
                    </Link>
                    <Link
                      to="/progress"
                      onClick={closeHeaderMenu}
                      className="flex items-center gap-3 px-4 py-2.5 rounded-xl text-gray-600 text-sm hover:bg-gray-50 transition-colors"
                    >
                      📊 Ma progression
                    </Link>
                    <Link
                      to="/level-test"
                      onClick={closeHeaderMenu}
                      className="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-purple-50 text-purple-700 font-medium text-sm hover:bg-purple-100 transition"
                    >
                      📋 Tester mon niveau
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl bg-red-50 text-red-600 font-medium text-sm hover:bg-red-100 transition"
                    >
                      🚪 Déconnexion
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      to="/login"
                      onClick={closeHeaderMenu}
                      className="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-primary-50 text-primary-700 font-medium text-sm hover:bg-primary-100 transition"
                    >
                      🔐 Connexion
                    </Link>
                    <Link
                      to="/register"
                      onClick={closeHeaderMenu}
                      className="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-green-50 text-green-700 font-medium text-sm hover:bg-green-100 transition"
                    >
                      📝 Inscription
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </header>
  );
};

export default Header;
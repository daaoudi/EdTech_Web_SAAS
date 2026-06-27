
import os
import pickle

def reset_miner():
    
    
    model_path = './tutor_ia_model/sequential_miner.pkl'
    backup_path = './tutor_ia_model/sequential_miner_backup.pkl'
    
    
    if os.path.exists(model_path):
        import shutil
        shutil.copy(model_path, backup_path)
        print(f"✅ Ancien fichier sauvegardé vers {backup_path}")
    
    
    new_data = {
        'patterns': [],
        'rules': [],
        'min_support': 0.10,
        'min_confidence': 0.60,
        'version': '2.0',
        'created_by': 'reset_script'
    }
    
    with open(model_path, 'wb') as f:
        pickle.dump(new_data, f)
    
    print(f"✅ Nouveau fichier créé: {model_path}")
    print(f"   Patterns: 0, Règles: 0")
    print("   Le système fonctionnera normalement et apprendra au fur et à mesure")

if __name__ == "__main__":
    reset_miner()
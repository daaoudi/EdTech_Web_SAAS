
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.sequential_miner import SequentialPatternMiner

def load_and_display_model():
    
    
    miner = SequentialPatternMiner()
    
    
    if miner.load('./tutor_ia_model/sequential_miner.pkl'):
        print("\n" + "="*60)
        print("📊 MODÈLE SEQUENTIAL PATTERN MINER")
        print("="*60)
        print(f"✅ Modèle chargé avec succès")
        print(f"   - Motifs trouvés: {len(miner.patterns)}")
        print(f"   - Règles générées: {len(miner.rules)}")
        print(f"   - Support minimum: {miner.min_support}")
        print(f"   - Confiance minimum: {miner.min_confidence}")
        
        
        if miner.patterns:
            print("\n📋 Top 5 motifs:")
            for i, pattern in enumerate(miner.patterns[:5]):
                print(f"   {i+1}. {pattern}")
        
        
        if miner.rules:
            print("\n📋 Top 5 règles (par confiance):")
            for i, rule in enumerate(miner.rules[:5]):
                print(f"   {i+1}. {rule['antecedent']} → {rule['consequent']}")
                print(f"       Confiance: {rule['confidence']:.2%}, Support: {rule['support']:.2%}")
        
        print("\n" + "="*60)
        return True
    else:
        print("❌ Échec du chargement du modèle")
        return False

if __name__ == "__main__":
    load_and_display_model()
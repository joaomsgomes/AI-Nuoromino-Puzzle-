import subprocess
import os
import glob

# Caminho da pasta dos testes
TEST_DIR = "sample"

# Caminho do teu programa (ajusta conforme necessário)
PROGRAM = "src/nuruomino.py"  # Substitui pelo nome correto do teu script principal

def run_test(input_file, expected_output_file):
    with open(input_file, 'r') as infile:
        process = subprocess.run(
            ['python3', PROGRAM],
            stdin=infile,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    
    with open(expected_output_file, 'r') as outfile:
        expected_output = outfile.read().strip()

    actual_output = process.stdout.strip()

    return actual_output == expected_output, actual_output, expected_output, process.stderr

def main():
    test_files = sorted(glob.glob(os.path.join(TEST_DIR, "test*.txt")))
    total = len(test_files)
    passed = 0

    for test_file in test_files:
        test_num = os.path.splitext(os.path.basename(test_file))[0][4:]  # extrai XX
        expected_file = os.path.join(TEST_DIR, f"test{test_num}.out")

        if not os.path.exists(expected_file):
            print(f"❌ Test {test_num}: ficheiro .out não encontrado.")
            continue
        
        result, actual, expected, stderr = run_test(test_file, expected_file)

        if result:
            print(f"✅ Test {test_num}: passou")
            passed += 1
        else:
            print(f"❌ Test {test_num}: falhou")
            print("Esperado:")
            print(expected)
            print("Obtido:")
            print(actual)
            if stderr:
                print("Erros:")
                print(stderr)

    print(f"\n{passed}/{total} testes passaram.")

if __name__ == "__main__":
    main()

from wad import WAD
from wad_loader import main as load_wad

def main():
    input = "../data/test.txt"
    output = "../data/test.wad"
    wad = WAD(input, 64)
    wad.build_wad(output)
    load_wad(output)

if __name__ == "__main__":
    main()
import pickle


def main():

    all_dicts = {}
    with open("all_textures.txt") as filehandle:
        current_map = ""
        map_dicts = {"Textures": [], "Flats": []}
        textures = True
        for line in filehandle.readlines():
            # print(line)

            line = line.rstrip()

            if line.startswith("Level"):
                # print(line)
                # current_map = line.split(" ")[1]
                # print(current_map)
                if current_map != "":
                    all_dicts[current_map] = map_dicts

                current_map = line.split(" ")[1]
                map_dicts = {"Textures": [], "Flats": []}

            if line.startswith("=="):
                if line.split(" ")[1] == "Textures":
                    print(line)
                    textures = True
                if line.split(" ")[1] == "Flats":
                    print(line)

                    textures = False
            number = line.split(".")
            if number[0].isdigit():
                # print(number)
                if textures:
                    map_dicts["Textures"].append(number[1].lstrip())
                else:
                    map_dicts["Flats"].append(number[1].lstrip())
            print(all_dicts)
    with open("all_map_textures.pkl", "wb") as saveloc:
        pickle.dump(all_dicts, saveloc)


if __name__=="__main__":
    main()

from pathlib import Path

import cv2 as cv
import json
import os
import shutil

mob_life_bar_path = str(Path(__file__).parent / "general" / "mob_life_bar.png")
user_target_bar_path = str(Path(__file__).parent / "general" / "user_target_bar.png")
inventory_perin_converter_path = str(Path(__file__).parent / "general" / "inventory_perin_converter.png")
inventory_icons_path = str(Path(__file__).parent / "general" / "inventory_icons.png")
target_mark_path = str(Path(__file__).parent / "general" / "target_mark.png")


class MobType:
    @staticmethod
    def get_type_list():
        return [name for name in vars(MobType) if not (name.startswith('__') and name.endswith('__')) and not callable(getattr(MobType, name))]
    
    @staticmethod
    def add_new_type(name: str, image_path: str):
        shutil.copyfile(image_path, str(Path(__file__).parent / "mob_types" / f"{name}.png"))
        MobType.load_types()

    @staticmethod
    def delete_mob_type(mob_type: str):
        MobInfo.delete_mobs_by_type(mob_type)
        os.remove(str(Path(__file__).parent / "mob_types" / f"{mob_type}.png"))
        delattr(MobType, mob_type)

    @staticmethod
    def load_types():
        folder = Path(__file__).parent / "mob_types"
        for file in folder.iterdir():
            if file.is_file():
                current_type_path = str(Path(__file__).parent / "mob_types" / file.name)
                setattr(MobType, file.name.split('.')[0], cv.imread(current_type_path, cv.IMREAD_GRAYSCALE))


MobType.load_types()


class MobInfo:
    @staticmethod
    def add_new_mob(name: str, map_name: str, image_path: str, height_offset: int, element: str) -> None:
        """
        Add new mob to json collection (mobs_list.json)
        """
        json_collection_path = str(Path(__file__).parent / "mobs_list.json")

        # copy image for cv detection in asset folder
        shutil.copyfile(image_path, str(Path(__file__).parent / "names" / f"{name}.png"))

        current_mobs_list = MobInfo.get_all_mobs()
        current_mobs_list[name] = {
            "name": name,
            "element": element,
            "map_name": map_name,
            "height_offset": height_offset
        }

        file = open(json_collection_path, 'w+')
        json.dump(current_mobs_list, file)
    
    @staticmethod
    def delete_mobs(name_list: list[str]) -> None:
        """
        Delete list of mobs from json collection (mobs_list.json)
        """
        json_collection_path = str(Path(__file__).parent / "mobs_list.json")
        current_mobs_list = MobInfo.get_all_mobs()
        new_mobs_list = {}

        # delete images for cv detection from asset folder
        for key in current_mobs_list:
            if key in name_list:
                os.remove(str(Path(__file__).parent / "names" / f"{key}.png"))
            else:
                new_mobs_list[key] = current_mobs_list[key]

        file = open(json_collection_path, 'w+')
        json.dump(new_mobs_list, file)

    @staticmethod
    def delete_mobs_by_type(mob_type: str) -> dict[str, dict]:
        mob_list_to_delete = [name for name, value in MobInfo.get_all_mobs().items() if value.get('element') == mob_type]
        MobInfo.delete_mobs(mob_list_to_delete)

    @staticmethod
    def get_all_mobs() -> dict[str, dict]:
        """
        Get a list of all mobs registered. Using a dump of mobs_list.json file

        :return: list of all mobs as dict (key: 'mob_name', val: params_dict)
        """
        json_collection_path = str(Path(__file__).parent / "mobs_list.json")

        # Check mobs_list.json
        if not os.path.isfile(json_collection_path):
            file = open(json_collection_path, 'w+')
            json.dump({}, file)
            file.close()

        mobs_list = json.load(open(json_collection_path, 'r'))
        return mobs_list


class GeneralAssets:
    MOB_LIFE_BAR = cv.imread(mob_life_bar_path, cv.IMREAD_GRAYSCALE)
    USER_TARGET_BAR = cv.imread(user_target_bar_path, cv.IMREAD_GRAYSCALE)
    INVENTORY_PERIN_CONVERTER = cv.imread(inventory_perin_converter_path, cv.IMREAD_GRAYSCALE)
    INVENTORY_ICONS = cv.imread(inventory_icons_path, cv.IMREAD_GRAYSCALE)
    TARGET_MARK = cv.imread(target_mark_path, cv.IMREAD_GRAYSCALE)

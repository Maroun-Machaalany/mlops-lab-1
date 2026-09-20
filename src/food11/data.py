from pathlib import Path
import shutil

from PIL import Image


RAW_DIR = Path("data/food11_raw")
PROCESSED_DIR = Path("data/food11_processed")
MINI_DIR = Path("data/food11_processed_mini")

CATEGORIES = {
    0: "Bread",
    1: "Dairy product",
    2: "Dessert",
    3: "Egg",
    4: "Fried food",
    5: "Meat",
    6: "Noodles-Pasta",
    7: "Rice",
    8: "Seafood",
    9: "Soup",
    10: "Vegetable-Fruit",
}

IMAGE_SIZE = (128, 128)
MAX_MINI_IMAGES = 100


def get_category(filename: str) -> str:
    """Extract the Food-11 category from the beginning of a filename."""
    category_id = int(filename.split("_")[0])
    return CATEGORIES[category_id]


def process_dataset():
    for split in ["training", "evaluation", "validation"]:
        raw_split = RAW_DIR / split
        processed_split = PROCESSED_DIR / split
        mini_split = MINI_DIR / split

        processed_split.mkdir(parents=True, exist_ok=True)
        mini_split.mkdir(parents=True, exist_ok=True)

        category_counts = {}

        for image_path in raw_split.iterdir():
            if not image_path.is_file():
                continue

            try:
                category = get_category(image_path.name)
            except (ValueError, KeyError):
                print(f"Skipping unknown file: {image_path}")
                continue

            processed_category_dir = processed_split / category
            mini_category_dir = mini_split / category

            processed_category_dir.mkdir(parents=True, exist_ok=True)
            mini_category_dir.mkdir(parents=True, exist_ok=True)

            output_path = processed_category_dir / image_path.name

            with Image.open(image_path) as image:
                image = image.convert("RGB")
                image = image.resize(IMAGE_SIZE)
                image.save(output_path)

            count = category_counts.get(category, 0)

            if count < MAX_MINI_IMAGES:
                mini_output_path = mini_category_dir / image_path.name
                shutil.copy2(output_path, mini_output_path)
                category_counts[category] = count + 1


if __name__ == "__main__":
    process_dataset()
    print("Food-11 data preparation completed successfully.")
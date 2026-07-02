import cv2
import os


def crop_invoice_number_areas(image_path, output_folder="static/processed"):
    image = cv2.imread(image_path)
    if image is None:
        return [image_path]

    os.makedirs(output_folder, exist_ok=True)

    h, w = image.shape[:2]

    # 直接從原圖抓可能的發票號碼區
    crop_ranges = [
        (0.08, 0.32),
        (0.10, 0.36),
        (0.12, 0.40),
        (0.15, 0.45),
        (0.18, 0.48),
    ]

    paths = []
    filename = os.path.basename(image_path)
    name, ext = os.path.splitext(filename)

    for i, (sy, ey) in enumerate(crop_ranges):
        x1 = int(w * 0.10)
        x2 = int(w * 0.90)
        y1 = int(h * sy)
        y2 = int(h * ey)

        area = image[y1:y2, x1:x2]

        area = cv2.resize(area, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(area, cv2.COLOR_BGR2GRAY)

        # 不要太強二值化，保留熱感紙字體
        gray = cv2.convertScaleAbs(gray, alpha=1.4, beta=5)

        output_path = os.path.join(output_folder, f"{name}_number_{i}{ext}")
        cv2.imwrite(output_path, gray)
        paths.append(output_path)

    return paths
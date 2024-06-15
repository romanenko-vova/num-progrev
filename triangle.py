import asyncio
from PIL import Image, ImageDraw, ImageFont
import math


async def calc_arkans(date):
    # первый ряд
    nums_lst = date.split(".")
    sum_day = sum([int(num) for num in nums_lst[0]])
    sum_month = int(nums_lst[1])
    sum_year = sum([int(num) for num in nums_lst[2]])
    if sum_year > 22:
        sum_year = sum([int(num) for num in str(sum_year)])
    # print(sum_day)
    # print(sum_month)
    # print(sum_year)
    first_row = [sum_day, sum_month, sum_year]

    # второй ряд
    num4 = sum_day + sum_month
    if num4 > 22:
        num4 = sum[[int(num) for num in str(num4)]]
    if sum_year > 9:
        num5 = sum([int(num) for num in str(sum_year)])
    else:
        num5 = sum_year
    second_row = [num4, num5]

    # третий ряд
    num6 = num5 + num4
    if num6 > 22:
        num6 = sum([int(num) for num in str(num6)])

    third_row = [num6]

    return first_row, second_row, third_row


def calc_money_code(date):
    nums_lst = date.split(".")

    money_code_lst = []
    for num in nums_lst:
        num = str(sum([int(x) for x in num]))
        while int(num) > 9:
            num = str(sum([int(x) for x in num]))
        money_code_lst.append(num)

    last_num = "".join(money_code_lst)
    while int(last_num) > 9:
        last_num = str(sum([int(x) for x in last_num]))
    money_code_lst.append(last_num)
    return "".join(money_code_lst)


async def create_triangle_image(
    id, date
):
    
    color_bg = "#206676"
    color_lines = "#FF7F00"
    color_font = "#cacaca"
    path_font = './font/Dudka Bold.ttf'
    path_img = "./triangles/"
    numbers = await calc_arkans(date)
    width, height = 600, 600

    image = Image.new("RGB", (width, height), color_bg)
    draw = ImageDraw.Draw(image)

    # Center of the image
    cx, cy = width // 2, height // 2

    # Side length of the equilateral triangle
    side_length = min(width, height) * 0.9  # 90% of the smaller dimension
    h = (math.sqrt(3) / 2) * side_length

    # Calculate the vertices of the equilateral triangle
    top_vertex = (cx, cy - h / 2)
    left_vertex = (cx - side_length / 2, cy + h / 2)
    right_vertex = (cx + side_length / 2, cy + h / 2)
    points = [top_vertex, left_vertex, right_vertex]

    # Adjusting the position to make the distances to the edges equal
    margin = (height - h) / 2
    top_vertex = (cx, margin)
    left_vertex = (cx - side_length / 2, height - margin)
    right_vertex = (cx + side_length / 2, height - margin)
    points = [top_vertex, left_vertex, right_vertex]

    # Draw the triangle using polygon to ensure sharp angles
    draw.polygon(points, outline=color_lines, fill=None, width=10)

    # Try to load the font
    try:
        font = ImageFont.truetype(path_font, size=65)
    except IOError:
        font = ImageFont.load_default()

    # Calculate positions for the numbers
    def interpolate(p1, p2, t):
        return (p1[0] * (1 - t) + p2[0] * t, p1[1] * (1 - t) + p2[1] * t)

    # Adjusted positions for numbers inside the triangle
    # Move rows lower and adjust the positions slightly for equal row spacing
    offset = h / 12
    bottom_row_y = (left_vertex[1] + top_vertex[1]) * 0.75 + offset
    middle_row_y = (left_vertex[1] + top_vertex[1]) * 0.5 + offset
    top_row_y = (left_vertex[1] + top_vertex[1]) * 0.25 + offset

    positions_bottom = [
        (cx - side_length / 3, bottom_row_y),
        (cx, bottom_row_y),
        (cx + side_length / 3, bottom_row_y),
    ]
    positions_middle = [
        (cx - side_length / 6, middle_row_y),
        (cx + side_length / 6, middle_row_y),
    ]
    position_top = [(cx, top_row_y)]

    positions = positions_bottom + positions_middle + position_top
    numbers_flat = [str(num) for sublist in numbers for num in sublist]

    for pos, num in zip(positions, numbers_flat):
        draw.text(pos, num, font=font, fill=color_font, anchor="mm")

    file_path = f"{path_img}{id}_tr.png"
    image.save(file_path)
    return numbers, file_path

async def make_arkans_flat_and_calc_unique(arkans) -> tuple[list[int], int]:
    flat = [*arkans[0], *arkans[1], *arkans[2]]
    flat_set = set(flat)
    return flat, len(set(flat_set))

if __name__ == "__main__":
    # nums = asyncio.run(calc_arkans("26.11.1999"))

    # asyncio.run(create_triangle_image(
    #     752,
    #     "26.11.1999"
    # ))

    print(calc_money_code("01.01.1999"))
    # print(make_arkans_flat_and_calc_unique(([8, 11, 10], [19, 1], [20])))

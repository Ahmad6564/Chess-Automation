import mss
from PIL import Image
from pynput import mouse

def capture_chessboard(center_x, center_y, board_size=800):
    """
    Capture the chessboard area based on center coordinates.
    board_size: estimated size of the chessboard (default 800 pixels)
    """
    # Calculate the region based on center point
    half_size = board_size // 2
    region = {
        "left": center_x - half_size,
        "top": center_y - half_size,
        "width": board_size,
        "height": board_size
    }
    
    with mss.mss() as sct:
        screenshot = sct.grab(region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        img.save("chessboard_capture.png")
        print(f"Chessboard captured and saved as 'chessboard_capture.png'")
        return img

def on_click(x, y, button, pressed):
    if pressed:
        print(f"Center coordinates: X: {x}, Y: {y}")
        with open("positions.txt", "a") as f:
            f.write(f"Center - X: {x}, Y: {y}\n")
        
        # Capture the chessboard using the clicked coordinates as center
        capture_chessboard(x, y)
        
        # Stop listener after first click
        return False

print("Click on the CENTER of the chessboard...")
print("The program will capture the board area and save it as 'chessboard_capture.png'")
with mouse.Listener(on_click=on_click) as listener:
    listener.join()
 
 
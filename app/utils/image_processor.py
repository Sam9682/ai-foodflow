from PIL import Image
import requests
from io import BytesIO
import os
from typing import Dict, Tuple

class ImageProcessor:
    """Handle image processing for different platform requirements"""
    
    PLATFORM_SPECS = {
        "uber_eats": {
            "max_size": (1200, 800),
            "aspect_ratio": (3, 2),
            "format": "JPEG",
            "quality": 85
        },
        "deliveroo": {
            "max_size": (1024, 1024),
            "aspect_ratio": (1, 1),
            "format": "JPEG",
            "quality": 90
        },
        "just_eat": {
            "max_size": (800, 600),
            "aspect_ratio": (4, 3),
            "format": "JPEG",
            "quality": 80
        }
    }
    
    @staticmethod
    def process_image_for_platform(image_url: str, platform: str, output_dir: str) -> str:
        """Process image according to platform specifications"""
        if platform not in ImageProcessor.PLATFORM_SPECS:
            raise ValueError(f"Platform {platform} not supported")
        
        specs = ImageProcessor.PLATFORM_SPECS[platform]
        
        # Download image
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        
        # Resize and crop to aspect ratio
        processed_image = ImageProcessor._resize_and_crop(image, specs["max_size"], specs["aspect_ratio"])
        
        # Save processed image
        filename = f"{platform}_{os.path.basename(image_url)}"
        output_path = os.path.join(output_dir, filename)
        
        processed_image.save(
            output_path,
            format=specs["format"],
            quality=specs["quality"],
            optimize=True
        )
        
        return output_path
    
    @staticmethod
    def _resize_and_crop(image: Image.Image, max_size: Tuple[int, int], aspect_ratio: Tuple[int, int]) -> Image.Image:
        """Resize and crop image to specified dimensions and aspect ratio"""
        target_width, target_height = max_size
        target_ratio = aspect_ratio[0] / aspect_ratio[1]
        
        # Calculate current aspect ratio
        current_ratio = image.width / image.height
        
        if current_ratio > target_ratio:
            # Image is wider than target, crop width
            new_width = int(image.height * target_ratio)
            left = (image.width - new_width) // 2
            image = image.crop((left, 0, left + new_width, image.height))
        elif current_ratio < target_ratio:
            # Image is taller than target, crop height
            new_height = int(image.width / target_ratio)
            top = (image.height - new_height) // 2
            image = image.crop((0, top, image.width, top + new_height))
        
        # Resize to target dimensions
        image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        return image
    
    @staticmethod
    def validate_image(image_url: str) -> Dict[str, any]:
        """Validate image format and dimensions"""
        try:
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))
            
            return {
                "valid": True,
                "format": image.format,
                "size": image.size,
                "mode": image.mode
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
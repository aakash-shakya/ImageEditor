from PIL import ImageFilter, ImageOps


class Filter:    
    @classmethod
    def grayscale(cls, current_image, history, display, log_activity, show_error):
        if current_image:
            try:
                current_image = current_image.convert("L")
                history(current_image)
                display(current_image)

                
                log_activity("Grayscale")
                return current_image
            except Exception as e:
                show_error(f"Error applying grayscale: {str(e)}")

    @classmethod
    def blur(cls, current_image, history, display, log_activity, show_error):
        if current_image:
            try:
                current_image = current_image.filter(ImageFilter.BLUR)
                history(current_image)
                display(current_image)

                log_activity("Blur")
                return current_image
            except Exception as e:
                show_error(f"Error applying blur: {str(e)}")

    @classmethod
    def sharpen(cls, current_image, history, display, log_activity, show_error):
        if current_image:
            try:
                current_image = current_image.filter(ImageFilter.SHARPEN)
                history(current_image)
                display(current_image)

                
                log_activity("Sharpen")
                return current_image
            except Exception as e:
                show_error(f"Error applying sharpen: {str(e)}")

    @classmethod
    def negative(cls, current_image, history, display, log_activity, show_error):
        if current_image:
            try:
                current_image = ImageOps.invert(current_image)
                history(current_image)
                display(current_image)

                
                log_activity("Negative")
                return current_image
            except Exception as e:
                show_error(f"Error applying negative: {str(e)}")
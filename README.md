# Advanced Image Editor

## Overview

The **Advanced Image Editor** is a Python-based application built using the PyQt5 framework and the Python Imaging Library (PIL). It provides a user-friendly interface for editing images with various adjustments, filters, and history tracking. The application supports both light and dark themes, making it visually appealing and customizable.

## Features

### **Image Editing Features**

- **Brightness, Contrast, and Saturation Adjustments**: Sliders to adjust image brightness, contrast, and saturation in real-time.

- **Filters**: Apply filters such as Grayscale, Blur, Sharpen, and Negative to the image.

- **Undo/Redo**: Easily undo or redo actions to revert or reapply changes.

- **Image History**: Track all actions performed on the image with timestamps in a history tree.

- **Delete Actions**: Remove specific actions from the history tree and revert the image accordingly.

### **User  Interface Features**

- **Themes**: Switch between light and dark themes for a personalized experience.

- **Dockable Panels**: Adjustments and filters are available in dockable panels for easy access.

- **Responsive Layout**: The application layout is flexible and adjusts to the window size.

- **Image Preview**: View the edited image in a scrollable area with zoom support.

### **File Management**

- **Open Image**: Load images in formats such as PNG, JPG, JPEG, BMP, and GIF.

- **Save Image**: Save the edited image in PNG, JPG, JPEG, or BMP format.

- **Save As**: Save the edited image with a new filename.

## Installation

### **Prerequisites**

- Python 3.x

- PyQt5

- Pillow (PIL)

### **Steps**

1\. Clone the repository:

   ```bash

   git clone https://github.com/your-repo/advanced-image-editor.git

   cd advanced-image-editor

   ```

2\. Install the required dependencies:

   ```bash

   pip install PyQt5 pillow

   ```

3\. Run the application:

   ```bash

   python image_editor.py

   ```

## Usage

### **Opening an Image**

- Go to **File > Open** or press `Ctrl+O` to open an image file.

### **Applying Adjustments**

- Use the sliders in the **Adjustments** dock to modify brightness, contrast, and saturation.

### **Applying Filters**

- Select a filter from the dropdown in the **Filters** dock to apply it to the image.

### **Saving an Image**

- Go to **File > Save** or press `Ctrl+S` to save the image.

- Use **File > Save As** or press `Ctrl+Shift+S` to save the image with a new filename.

### **Undo/Redo**

- Use **Edit > Undo** (`Ctrl+Z`) or **Edit > Redo** (`Ctrl+Y`) to revert or reapply changes.

### **Switching Themes**

- Go to **Preferences > Theme** and select either **Light** or **Dark** theme.

### **Deleting Actions**

- Hover over an action in the history tree and click the delete icon to remove it.

## Screenshots

### **Light Theme**

![Light Theme Screenshot](screenshots/light_theme.png)

### **Dark Theme**

![Dark Theme Screenshot](screenshots/dark_theme.png)

## Logging

The application logs all activities to `image_editor.log` for debugging and tracking purposes.

## Contributing

Contributions are welcome! Please follow these steps:

1\. Fork the repository.

2\. Create a new branch for your feature or bugfix.

3\. Submit a pull request with a detailed description of your changes.

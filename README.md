# Web Store - Django E-commerce Project

This is a full-featured e-commerce website built with the Django framework. It includes product management, a shopping cart, a checkout process with Stripe integration, user profiles, and more.

## Features

*   **Product Catalog:** Browse products by category.
*   **Shopping Cart:** Add/remove products to a session-based shopping cart.
*   **User Authentication:** Register, log in, log out, and reset passwords.
*   **User Profiles:** Manage personal information and view order history.
*   **Checkout:** Complete order process with shipping information.
*   **Payment Integration:** Supports payments via Stripe.
*   **Coupon System:** Apply discount codes to orders.
*   **Wishlist:** Save products for later.
*   **Product Reviews:** Users can rate and review products.

## Project Structure

```
web-store/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── store/                 # Core application
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── admin.py
│   ├── models.py          # Database schema
│   ├── views.py           # Application logic
│   └── urls.py            # App-specific URLs
└── web_store/             # Project configuration
    ├── settings.py        # Project settings
    └── urls.py            # Root URL configuration
```

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.8+
*   pip (Python package installer)

### Installation & Setup

1.  **Clone the repository (or download the source code):**
    ```bash
    git clone <repository-url>
    cd web-store
    ```

2.  **Create and activate a virtual environment:**
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply database migrations:**
    This will create the necessary tables in the database based on the models defined in `store/models.py`.
    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser account:**
    This account will have access to the Django admin interface.
    ```bash
    python manage.py createsuperuser
    ```
    You will be prompted to enter a username, email, and password.

### Running the Development Server

Once the setup is complete, you can run the development server:

```bash
python manage.py runserver
```

The website will be available at `http://127.0.0.1:8000/`.

### Accessing the Admin Panel

To manage products, categories, orders, and users, you can access the Django admin panel:

1.  Make sure the development server is running.
2.  Navigate to `http://127.0.0.1:8000/admin/`.
3.  Log in with the superuser credentials you created earlier.

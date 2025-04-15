# Mind-vs-Wild

Follow these steps to run the project :

1. Clone the repository
2. Go to the api folder
    ```bash
    cd api
    ```
3. Copy the `.env-lan-example` file to `.env.lan`
    ```bash
    cp .env-lan-example .env.lan
    ```
4. Generate a secret key
    ```bash
    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    ```
5. In the `.env.lan` file, set the `SECRET_KEY` variable to the generated secret key (prefix it with `django-insecure-` if used for development)
    ```bash
    SECRET_KEY=django-insecure-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    ```
6. In the `.env.lan` file, add your local IP address to the indicated variables, also replace any other IP address that is not the loopback address
7. Go to the frontend folder
    ```bash
    cd ../frontend
    ```
8. Copy the `.env-lan-example` file to `.env.lan`
    ```bash
    cp .env-lan-example .env.lan
9. In the `.env.lan` file, add your local IP address to the indicated variables, also replace any other IP address that is not the loopback address
10. Go back to the root folder
    ```bash
    cd ..
    ```
11. Run the Docker containers
    ```bash
    docker-compose up -d --build
    ```
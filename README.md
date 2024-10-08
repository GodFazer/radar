# radar
![image](https://github.com/user-attachments/assets/5e4fee56-3604-46cc-b8a6-e24a619cf232)
## Огляд
Цей проект є веб-додатком радару, який візуалізує дані в реальному часі за допомогою графіка. Він інтегрує Flask для бекенду та використовує WebSocket для постійного отримання та передачі даних. Додаток дозволяє користувачам налаштовувати параметри збору даних, переглядати живі оновлення на радарному графіку та динамічно керувати конфігураціями.

## Особливості
Візуалізація Даних у Реальному Часі: Відображає дані на радарному графіку, оновлюючи його кожну секунду на основі вхідних повідомлень WebSocket.

Управління Конфігурацією: Користувачі можуть вводити налаштування конфігурації (наприклад, кількість вимірювань за оберт, швидкість обертання, швидкість цілей), які надсилаються на WebSocket сервер для обробки.

Адаптивний Дизайн: Додаток адаптується до різних розмірів екранів для оптимального перегляду як на настільних, так і на мобільних пристроях.
Обробка Помилок: Додаток надає зворотний зв'язок у випадку виникнення помилок під час отримання даних або надсилання конфігурацій.

## Технології
Фронтенд:
HTML, CSS та JavaScript
Plotly.js для візуалізації даних
jQuery для маніпуляцій з DOM та AJAX запитів

Бекенд:
Flask для обробки HTTP запитів та сервісу веб-додатку
WebSocket для зв'язку в реальному часі

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from modules.email import EmailModule
from modules.sms import SMSModule
import uvicorn
import pika
import json

# Инициализация модулей
email_module = EmailModule(
    smtp_server="smtp.example.com", 
    smtp_port=587, 
    username="your-email@example.com", 
    password="your-password"
)
sms_module = SMSModule(api_key="your-sms-api-key")


# Создаем приложение FastAPI
app = FastAPI()


# Инициализация FastAPI
app = FastAPI()

# Подключение к RabbitMQ
def get_rabbitmq_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))  # подключаемся к локальному RabbitMQ
    channel = connection.channel()
    channel.queue_declare(queue="notifications", durable=True)  # Объявляем очередь, если она не существует
    return connection, channel

# Модель для запроса
class NotificationRequest(BaseModel):
    channel: str  # Канал (email, sms, push)
    recipient: str  # Получатель
    message: str  # Сообщение

# Эндпоинт для отправки уведомлений
@app.post("/send-notification/")
def send_notification(request: NotificationRequest):
    try:
        connection, channel = get_rabbitmq_connection()

        # Создаём сообщение для RabbitMQ
        message = {
            "channel": request.channel,
            "recipient": request.recipient,
            "message": request.message
        }

        # Публикуем сообщение в очередь RabbitMQ
        channel.basic_publish(
            exchange="",  # используем default exchange
            routing_key="notifications",  # очередь, в которую будем отправлять
            body=json.dumps(message),  # сообщение в формате JSON
            properties=pika.BasicProperties(
                delivery_mode=2,  # Сообщение будет сохранено на диск
            )
        )

        connection.close()
        return {"message": "Notification queued successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue notification: {str(e)}")
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

import pika
import json
from modules.email import EmailModule  # модуль отправки email
from modules.sms import SMSModule  # модуль отправки SMS

# Создание объектов модулей отправки
email_module = EmailModule(
    smtp_server="smtp.example.com",
    smtp_port=587,
    username="your-email@example.com",
    password="your-password"
)
sms_module = SMSModule(api_key="your-sms-api-key")

# Обработчик сообщений
def process_notification(message):
    """
    Обрабатываем уведомление в зависимости от канала (email, sms и т.д.)
    """
    if message["channel"] == "email":
        success = email_module.send(message["recipient"], message["message"])
    elif message["channel"] == "sms":
        success = sms_module.send(message["recipient"], message["message"])
    else:
        print(f"Unsupported channel: {message['channel']}")
        success = False

    if success:
        print(f"Notification sent successfully: {message}")
    else:
        print(f"Failed to send notification: {message}")

# Основной процесс воркера
def start_worker():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    # Подписываемся на очередь
    channel.queue_declare(queue="notifications", durable=True)

    print("Worker started. Waiting for messages...")

    def callback(ch, method, properties, body):
        """
        Получаем сообщение и передаем его для обработки
        """
        print(f"Received message: {body}")
        message = json.loads(body)
        process_notification(message)

        # Подтверждаем, что сообщение было обработано
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # Консьюмер на очереди "notifications"
    channel.basic_consume(queue="notifications", on_message_callback=callback)
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()

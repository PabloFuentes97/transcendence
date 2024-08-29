export default function (message){
    const notificationContainer = document.getElementById("notificationContainer")
    if (!notificationContainer)
        return;

    const notification = document.createElement('div');
    notification.classList.add('tc-notification');
    notification.classList.add('tc-border');
    notification.textContent = message;
    
    notificationContainer.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('fade');
        setTimeout(() => {
            notificationContainer.removeChild(notification);
        }, 300);
    }, 3000);
}
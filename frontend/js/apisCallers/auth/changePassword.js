

export default async(newPassword, oldPassword) => {
    const response = fetch('/auth_service/change_password/',{
        method: 'POST',
        headers:{
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
        },
        body: JSON.stringify({ old_password: oldPassword, new_password: newPassword})
    })
    return (await response).status;
}
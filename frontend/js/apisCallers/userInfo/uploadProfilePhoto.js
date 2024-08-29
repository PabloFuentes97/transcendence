
export default async(file) => {

    const formData = new FormData();
    formData.append('file', file);


    const response = fetch('/user_info/upload_profile_photo',{
        method: 'POST',
        headers:{
            'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
        },
        body: formData
    })
    
    if (!(await response).ok)
        console.error('API response not ok: ' + (await response).statusText.message);
    return (await response).status;
}
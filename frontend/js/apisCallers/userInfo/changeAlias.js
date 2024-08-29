

export default async(alias) => {
    
    try{
        const response = fetch('/user_info/change_alias',{
            method: 'PATCH',
            headers:{
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
            },
            body: JSON.stringify({alias: alias})
        });
        if (!(await response).ok)
            throw new Error('API response not ok: ' + (await response).statusText);
        const data = (await response).json();
        return data;
    }
    catch (error){
        console.error('Error:', error.message);
        return null;
    }
}
export default async() => {
    try{
        
        let url = '/user_info/get_all_users_info?order_by=elo&limit=10';

        const response = fetch(url,{
            method: 'GET',
            headers:{
                'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')

            }
        })
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
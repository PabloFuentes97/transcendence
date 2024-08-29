
export default async(endpoint, query) => {
    try{
        
        let url = '/user_info/' + endpoint;
        if (query != null && query != '')
            url += "?" + query;

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
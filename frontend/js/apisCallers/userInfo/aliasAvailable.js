export default async(alias) => {

    try{
        
        let url = '/user_info/alias_available?alias=' + alias;

        const response = await fetch(url,{
            method: 'GET',
            headers:{
                'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
            }
        })
        if (!await response.ok)
        {
            let res = await response.json()
            throw new Error(res.error);
        }
        return "ok";
    }
    catch (error){
        console.error('Error:', error.message);
        return error.message;
    }

    
}
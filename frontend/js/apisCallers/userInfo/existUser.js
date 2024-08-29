import userInfoGet from "./userInfoGet.js";

export default async(user) => {
    
    const data = await userInfoGet('exist_alias', 'username=' + user);

    if (data == null)
        return false;
    if (data.answer == "user exist")
        return true;
    return false;
}
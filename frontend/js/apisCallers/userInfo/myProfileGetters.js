import getMyUserInfo from "./getMyUserInfo.js";

export async function getMyAlias(){
    const data = await getMyUserInfo();
    if (data)
        return data.alias;
    return false;
}

export async function getMyProfilePicture(){
    const data = await getMyUserInfo();
    if (data)
        return data.photo_profile;
    return false;
}

export async function getMyUsername(){
    const data = await getMyUserInfo();
    if (data)
        return data.username;
    return false;
}

export async function elo(){
    const data = await getMyUserInfo();
    if (data)
        return data.elo;
    return false;
}

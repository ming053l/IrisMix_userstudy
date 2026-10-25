export function adminAuthState(user,configuredEmail){
 const owner=typeof configuredEmail==='string'?configuredEmail.trim().toLowerCase():'';
 if(!owner)return {kind:'unconfigured'};
 if(!user?.userId||!user?.email)return {kind:'anonymous'};
 return user.email.trim().toLowerCase()===owner?{kind:'owner'}:{kind:'forbidden'};
}

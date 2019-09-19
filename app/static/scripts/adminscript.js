/** Ban a given user after getting confirmation **/
function BanUser(banLink)
{
    confirmation = confirm("Are you sure you want to ban this user?")
    if(confirmation) window.location.href=banLink;
    else return;
}
/** Unban a given user after getting confirmation **/
function UnbanUser(unbanLink)
{
    confirmation = confirm("Are you sure you want to unban this user?")
    if(confirmation) window.location.href=unbanLink;
    else return;
}
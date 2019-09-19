/** Get company value on click **/
function SetCompanyValue(companyId, elementId)
{
    document.getElementById(elementId).value=companyId;
}
/** Clear values of form with given ID **/
function ClearForm(formId)
{
    document.getElementById(formId).reset();
}
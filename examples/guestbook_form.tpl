{* Smarty *}

<form action="{$SCRIPT_NAME}?action=submit" method="post">

<table border="1">

    {if $error ne ""}
        <tr>
            <td bgcolor="yellow" colspan="2">
                {if $error eq "name_empty"}You must supply a name.
                {elseif $error eq "comment_empty"} You must supply a comment.
                {/if}
            </td>
        </tr>
    {/if}
    <tr>
        <td>Name:</td>
        <td><input type="text" name="Name" value="{$post.Name|escape}" size="40"></td>
    </tr>
    <tr>
        <td valign="top">Comment:</td>
        <td><textarea name="Comment" cols="40" rows="10">{$post.Comment|escape}</textarea></td>
    </tr>
    <tr>
        <td colspan="2" align="center"><input type="submit" value="Submit"></td>
    </tr>

</table>


</form>

{literal}
	<script type="text/javascript">
		var $foo = $('.bar');
		var bar = function() {
			console.log('Hello World!');
		}
	</script>
{/literal}
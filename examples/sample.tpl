{foreach item="banana" from=$charlene|hello:awesome }
	<b>Hello Charlene {banana.peel|hello:blue:green|upcase:hey}</b>
{/foreach}
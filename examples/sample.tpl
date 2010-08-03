<h2>Sales Qualifications</h2>

<table width="100%" align="center" cellpadding="0" cellspacing="0" class="listTable">
	<tr align="right">
		<th align="left">systemid</th>
		<th align="left">company name</th>
		<th align="left">Owner Name</th>
		<th align="left">Email</th>
		<th align="left">phone #</th>
		<th align="left">type</th>
	</tr>
	{foreach from=$systems item=system}
	<tr>
		<td>{$system.systemid}</td>
		<td>{create_link url=$system.subdomain name=$system.name}</td>
		<td>{$system.owner_name}</td>
		<td>{mailto address=$system.info_email}</td>
		<td>{$system.bus_phone}</td>
		<td>{$types[$system.business_type]}</td>
	</tr>
	{/foreach}
</table>
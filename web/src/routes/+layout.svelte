<script lang="ts">
  import '../app.css'
	import { invalidate } from '$app/navigation'
	import { onMount } from 'svelte'

	let { data, children } = $props()
	let { supabase, claims } = $derived(data)
	onMount(() => {
		const { data } = supabase.auth.onAuthStateChange((event, _session) => {
			if (_session?.expires_at !== claims?.expires_at) {
				invalidate('supabase:auth')
			}
		})
		return () => data.subscription.unsubscribe()
	})

</script>

<svelte:head>
	<title>User Management</title>
</svelte:head>

<div>
	{@render children()}
</div>

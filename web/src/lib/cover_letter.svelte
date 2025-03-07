<script lang="ts">
  import { onMount } from "svelte";
  import Spacer from "./spacer.svelte";

  import { store } from "./store.svelte";

  let isLoading = $state(false);
  const { file } = store;
  const { coverLetter, setCoverLetter, description } = $props();

  onMount(async () => {
    if (coverLetter) {
      return;
    }
    isLoading = true;
    const url = new URL(
      "https://jobmatch-api.orangemoss-fa3f1656.eastus.azurecontainerapps.io/api/v1/generate/cover-letter"
    );

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("job_description", description);
    console.log("loading");
    const res = await fetch(url, {
      headers: {
        Accept: "application/json",
      },
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    setCoverLetter(data.analysis);
    isLoading = false;
  });
</script>

<div>
  {#if isLoading}
    <p>Generating cover letter</p>
  {:else}
    <p class="font-600 text-24px">Cover letter</p>
    <Spacer size={8} axis="y" />
    <p class="whitespace-pre-line">
      {coverLetter}
    </p>
  {/if}
</div>

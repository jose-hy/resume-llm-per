<script lang="ts">
  import { onMount } from "svelte";
  import Spacer from "./spacer.svelte";

  let isLoading = $state(false);

  const { coverLetter, setCoverLetter, description, file } = $props();

  onMount(async () => {
    if (coverLetter) {
      return;
    }
    isLoading = true;
    const url = new URL(
      "https://jobmatch-api.orangemoss-fa3f1656.eastus.azurecontainerapps.io/api/v1/generate/cover-letter",
    );

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("job_description", description);

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
    <div class="flex items-center gap-2">
      <p>Generating cover letter</p>
      <div
        class="border-t-[black] border-l-[black] border-b-[black]
        w-[16px] h-[16px] border-[2px] border-transparent
        spinner animate-spin rounded-circle"
      ></div>
    </div>
  {:else}
    <p class="font-600 text-24px">Cover letter</p>
    <Spacer size={8} axis="y" />
    <p class="whitespace-pre-line">
      {coverLetter}
    </p>
  {/if}
</div>

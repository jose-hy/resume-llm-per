<script lang="ts">
  import { marked } from "marked";
  import { onMount } from "svelte";

  import { store } from "./store.svelte";
  import Spacer from "./spacer.svelte";

  let isLoading = $state(false);
  const { file } = store;
  const {
    improvement,
    disqualification,
    setImprovement,
    setDisqualification,
    description,
  } = $props();

  const getData = async (endpoint: string, formData: FormData) => {
    const res = await fetch(
      "https://jobmatch-api.orangemoss-fa3f1656.eastus.azurecontainerapps.io/api/v1/analyze/" +
        endpoint,
      {
        headers: {
          Accept: "application/json",
        },
        method: "POST",
        body: formData,
      }
    );

    return await res.json();
  };

  onMount(async () => {
    if (improvement || disqualification) {
      return;
    }
    isLoading = true;

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("job_description", description);

    console.log("loading");

    const [disqualificationData, improvementData] = await Promise.all([
      getData("disqualification", formData),
      getData("improvement", formData),
    ]);

    setDisqualification(disqualificationData.analysis);
    setImprovement(improvementData.analysis);
    isLoading = false;
  });
</script>

<div>
  {#if isLoading}
    <p>Analyzing resume</p>
  {:else}
    <p class="font-600 text-24px">Disqualifications</p>
    <Spacer size={8} axis="y" />
    {@html marked(disqualification)}
    <Spacer size={24} axis="y" />
    <p class="font-600 text-24px">Suggested improvements</p>
    <Spacer size={8} axis="y" />
    {@html marked(improvement)}
  {/if}
</div>

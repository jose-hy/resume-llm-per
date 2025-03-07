<script lang="ts">
  let { axis, size } = $props();

  let width = $state(size);
  let height = $state(size);

  if (axis === "x") {
    height = 0;
  } else if (axis === "y") {
    width = 0;
  }
</script>

<span
  style={`min-height: ${height}px; height: ${height}px; min-width: ${width}px; width: ${width}px; display: block;`}
></span>

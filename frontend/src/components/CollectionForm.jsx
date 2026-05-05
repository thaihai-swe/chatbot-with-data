import { useState } from "react";

function CollectionForm({ onSubmit }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    if (!name.trim()) {
      return;
    }
    await onSubmit({ name, description });
    setName("");
    setDescription("");
  }

  return (
    <form className="surface-card" onSubmit={handleSubmit}>
      <h3>Create collection</h3>
      <label className="field">
        <span>Name</span>
        <input value={name} onChange={(event) => setName(event.target.value)} />
      </label>
      <label className="field">
        <span>Description</span>
        <textarea
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />
      </label>
      <button className="button" type="submit">
        Add collection
      </button>
    </form>
  );
}

export default CollectionForm;

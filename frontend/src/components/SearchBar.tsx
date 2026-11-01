/**
 * Search bar for the board. Queries the task search endpoint as the user types
 * and shows a dropdown of matching tasks with a highlighted snippet.
 */
import { useState, type JSX } from "react";

import { searchTasks } from "../api/client";
import styles from "../styles/SearchBar.module.css";

interface SearchBarProps {
  onSelect: (taskId: number) => void;
}

export default function SearchBar({ onSelect }: SearchBarProps): JSX.Element {
  const [query, setQuery] = useState<string>("");
  const [results, setResults] = useState<any[]>([]);
  const [open, setOpen] = useState<boolean>(false);

  const handleChange = async (value: string) => {
    setQuery(value);
    if (value.trim() === "") {
      setResults([]);
      setOpen(false);
      return;
    }
    const data = await searchTasks(value);
    console.log("search results", data);
    setResults(data.results);
    setOpen(true);
  };

  return (
    <div className={styles.searchBar}>
      <input
        type="text"
        className={styles.input}
        placeholder="Search tasks…"
        value={query}
        onChange={(event) => handleChange(event.target.value)}
        aria-label="Search tasks"
      />

      {open && results.length > 0 && (
        <ul className={styles.results}>
          {results.map((hit: any) => (
            <li className={styles.result} onClick={() => onSelect(hit.task.id)}>
              <span className={styles.resultTitle}>{hit.task.title}</span>
              <span
                className={styles.resultSnippet}
                dangerouslySetInnerHTML={{ __html: hit.snippet }}
              />
            </li>
          ))}
        </ul>
      )}

      {open && results.length === 0 && (
        <ul className={styles.results}>
          <li className={styles.empty}>No matches</li>
        </ul>
      )}
    </div>
  );
}

/**
 * Unit tests for the TaskCard component.
 */
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import TaskCard from "../components/TaskCard";
import type { Task } from "../types";

function makeTask(overrides: Partial<Task> = {}): Task {
  return {
    id: 1,
    title: "Write the keynote outline",
    description: "Draft the three core sections",
    status: "todo",
    priority: "high",
    project_id: 10,
    assignee_id: null,
    due_date: "2026-06-15T00:00:00Z",
    created_at: "2026-05-01T09:00:00Z",
    updated_at: "2026-05-02T09:00:00Z",
    ...overrides,
  };
}

describe("TaskCard", () => {
  it("renders the title, description and priority", () => {
    render(<TaskCard task={makeTask()} onMove={vi.fn()} onDelete={vi.fn()} />);

    expect(screen.getByText("Write the keynote outline")).toBeInTheDocument();
    expect(screen.getByText("Draft the three core sections")).toBeInTheDocument();
    expect(screen.getByLabelText("Priority: high")).toHaveTextContent("high");
  });

  it("omits the description block when there is no description", () => {
    render(<TaskCard task={makeTask({ description: null })} onMove={vi.fn()} onDelete={vi.fn()} />);

    expect(screen.queryByText("Draft the three core sections")).not.toBeInTheDocument();
  });

  it("offers move actions for the other two statuses", () => {
    render(<TaskCard task={makeTask({ status: "todo" })} onMove={vi.fn()} onDelete={vi.fn()} />);

    expect(screen.getByRole("button", { name: "→ In Progress" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "→ Done" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "→ To Do" })).not.toBeInTheDocument();
  });

  it("calls onMove with the target status when a move button is clicked", () => {
    const onMove = vi.fn();
    render(<TaskCard task={makeTask({ id: 42, status: "todo" })} onMove={onMove} onDelete={vi.fn()} />);

    fireEvent.click(screen.getByRole("button", { name: "→ In Progress" }));

    expect(onMove).toHaveBeenCalledTimes(1);
    expect(onMove).toHaveBeenCalledWith(42, "in_progress");
  });

  it("calls onDelete with the task id when delete is clicked", () => {
    const onDelete = vi.fn();
    render(<TaskCard task={makeTask({ id: 7 })} onMove={vi.fn()} onDelete={onDelete} />);

    fireEvent.click(screen.getByRole("button", { name: "Delete Write the keynote outline" }));

    expect(onDelete).toHaveBeenCalledWith(7);
  });
});

import { useState, useCallback } from 'react';
import { ReactFlow, applyNodeChanges, applyEdgeChanges, addEdge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import '@/index.css';
import { Button } from '@/components/ui/button';
import {
	AlertDialog,
	AlertDialogAction,
	AlertDialogCancel,
	AlertDialogContent,
	AlertDialogDescription,
	AlertDialogFooter,
	AlertDialogHeader,
	AlertDialogTitle,
	AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

import { toast } from "sonner"
import { Badge } from "@/components/ui/badge"
import {
	Dialog,
	DialogClose,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"


const initialNodes = [
	{ id: 'n1', position: { x: 0, y: 0 }, data: { label: 'Content Generator' } },
	{ id: 'n2', position: { x: 0, y: 100 }, data: { label: 'Post Blog' } },
	{ id: 'n3', position: { x: 0, y: 200 }, data: { label: 'Email Notification to Subscribers' } },
];
const initialEdges = [{ id: 'n1-n2', source: 'n1', target: 'n2' }, { id: 'n2-n3', source: 'n2', target: 'n3' }];

export default function App() {
	const [nodes, setNodes] = useState(initialNodes);
	const [edges, setEdges] = useState(initialEdges);

	const onNodesChange = useCallback(
		(changes) => setNodes((nodesSnapshot) => applyNodeChanges(changes, nodesSnapshot)),
		[],
	);
	const onEdgesChange = useCallback(
		(changes) => setEdges((edgesSnapshot) => applyEdgeChanges(changes, edgesSnapshot)),
		[],
	);
	const onConnect = useCallback(
		(params) => setEdges((edgesSnapshot) => addEdge(params, edgesSnapshot)),
		[],
	);

	return (
		<>
			<h1 className="text-blue-500">Hello AutoMesh!</h1>
			<Button
				variant="outline"
				onClick={() =>
					toast("Event has been created", {
						description: "Sunday, December 03, 2023 at 9:00 AM",
						action: {
							label: "Undo",
							onClick: () => console.log("Undo"),
						},
					})
				}
			>
				Show Toast
			</Button>

			<AlertDialog>
				<AlertDialogTrigger asChild>
					<Button className="m-4" variant="outline">Show Dialog</Button>
				</AlertDialogTrigger>
				<AlertDialogContent>
					<AlertDialogHeader>
						<AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
						<AlertDialogDescription>
							This action cannot be undone. This will permanently delete your account
							and remove your data from our servers.
						</AlertDialogDescription>
					</AlertDialogHeader>
					<AlertDialogFooter>
						<AlertDialogCancel>Cancel</AlertDialogCancel>
						<AlertDialogAction>Continue</AlertDialogAction>
					</AlertDialogFooter>
				</AlertDialogContent>
			</AlertDialog>

			<Dialog>
				<form>
					<DialogTrigger asChild>
						<Button variant="lime">Open Dialog</Button>
					</DialogTrigger>
					<DialogContent className="sm:max-w-[425px]">
						<DialogHeader>
							<DialogTitle>Refund payment</DialogTitle>
							<DialogDescription>
								The refund will be reflected in the customer's bank account 2 to 3
								business days after processing.
							</DialogDescription>
						</DialogHeader>
						{/* <div className="grid gap-4">
							<div className="grid gap-3">
								<Label htmlFor="name-1">Name</Label>
								<Input id="name-1" name="name" defaultValue="Pedro Duarte" />
							</div>
							<div className="grid gap-3">
								<Label htmlFor="username-1">Username</Label>
								<Input id="username-1" name="username" defaultValue="@peduarte" />
							</div>
						</div> */}
						<DialogFooter>
							<DialogClose asChild>
								<Button variant="outline">Cancel</Button>
							</DialogClose>
							<Button type="submit">Refund</Button>
						</DialogFooter>
					</DialogContent>
				</form>
			</Dialog>

			{/* <Dialog>
				<DialogTrigger asChild>
					<Button variant="outline">Share</Button>
				</DialogTrigger>
				<DialogContent className="sm:max-w-md">
					<DialogHeader>
						<DialogTitle>Share link</DialogTitle>
						<DialogDescription>
							Anyone who has this link will be able to view this.
						</DialogDescription>
					</DialogHeader>
					<div className="flex items-center gap-2">
						<div className="grid flex-1 gap-2">
							<Label htmlFor="link" className="sr-only">
								Link
							</Label>
							<Input
								id="link"
								defaultValue="https://ui.shadcn.com/docs/installation"
								readOnly
							/>
						</div>
					</div>
					<DialogFooter className="sm:justify-start">
						<DialogClose asChild>
							<Button type="button" variant="secondary">
								Close
							</Button>
						</DialogClose>
					</DialogFooter>
				</DialogContent>
			</Dialog> */}

			<div className="mt-5 flex gap-3">
				<Badge variant="lime">documentation</Badge>
				<Badge variant="purple">help wanted</Badge>
				<Badge variant="rose">bug</Badge>
			</div>
			<div style={{ width: '100vw', height: '100vh' }}>
				<ReactFlow
					nodes={nodes}
					edges={edges}
					onNodesChange={onNodesChange}
					onEdgesChange={onEdgesChange}
					onConnect={onConnect}
					fitView
				/>
			</div>
		</>
	);
}
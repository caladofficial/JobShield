export default function JobDetailPage({ params }: { params: { id: string } }) {
  return (
    <div>Job Detail: {params.id}</div>
  )
}
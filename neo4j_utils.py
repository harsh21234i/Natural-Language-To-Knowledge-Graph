from neo4j import GraphDatabase

class Neo4jConnector:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_node(self, label, properties):
        """
        Create a node in Neo4j with the given label and properties.
        """
        query = f"MERGE (n:{label} {{name: $name}}) RETURN n"
        with self.driver.session() as session:
            session.run(query, properties)

    def create_relationship(self, label1, properties1, label2, properties2, rel_type):
        """
        Create a relationship between two nodes in Neo4j.
        """
        query = (
            f"MATCH (a:{label1} {{name: $name1}}), (b:{label2} {{name: $name2}}) "
            f"MERGE (a)-[r:{rel_type}]->(b) RETURN r"
        )
        with self.driver.session() as session:
            session.run(query, {"name1": properties1["name"], "name2": properties2["name"]})

    def get_graph_data(self):
        """
        Fetch nodes and relationships from Neo4j.
        """
        query = """
        MATCH (n)-[r]->(m)
        RETURN DISTINCT n, r, m
        """
        with self.driver.session() as session:
            result = session.run(query)
            nodes = []
            edges = []
            seen_nodes = set()

            for record in result:
                # Extract source node
                source = {
                    "id": record["n"].element_id,  # Use element_id for Neo4j 5.x+
                    "label": list(record["n"].labels)[0],
                    "properties": dict(record["n"]),
                }
                if source["id"] not in seen_nodes:
                    nodes.append(source)
                    seen_nodes.add(source["id"])

                # Extract target node
                target = {
                    "id": record["m"].element_id,  # Use element_id for Neo4j 5.x+
                    "label": list(record["m"].labels)[0],
                    "properties": dict(record["m"]),
                }
                if target["id"] not in seen_nodes:
                    nodes.append(target)
                    seen_nodes.add(target["id"])

                # Extract relationship
                edges.append({
                    "source": source["id"],
                    "target": target["id"],
                    "type": record["r"].type,
                    "properties": dict(record["r"]),
                })

            return {"nodes": nodes, "edges": edges}
import React, { useState, useEffect } from "react";
import axios from "axios";

const NewImages = ({ isTraslape, file }) => {
  const [conTraslape, setConTraslape] = useState(isTraslape);
  const [selectedFile, setSelectedFile] = useState(file);
  const [loading, setLoading] = useState(false);
  const [dataImages, setDataImages] = useState([]);

  const getImages = async () => {
    if (!selectedFile) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("image", selectedFile);
    formData.append("overlap", String(conTraslape));

    try {
      const response = await axios.post(
        "http://localhost:5000/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      const {data} = response
      setDataImages(data)
      //Actualizar el estado de imágenes
//    setDataImages((prevDataImages) => [
//      ...prevDataImages,
//      ...data.map(operations => ({
//        binary_image: operations.binary_image,
//        closed_image: operations.closed_image,
//        compound_image: operations.compound_image,
//        gray_image: operations.gray_image,
//        message: operations.message,
//        num_objects: operations.num_objects,
//        opened_image: operations.opened_image,
//        processed_image: operations.processed_image,
//      })),
//    ]);
    } catch (error) {
      console.error("Error al procesar la imagen:", error);
      alert(
        `Error al procesar la imagen: ${
          error.response?.data?.error || error.message
        }`
      );
    } finally {
      setLoading(false);
    }
  };

  // Use effect para llamar a getImages cuando se seleccione un archivo
  useEffect(() => {
    if (selectedFile) {
      getImages();
    }
  }, [selectedFile, conTraslape]); // Dependencias para que se ejecute cuando cambien

  return (
    <>
      {loading && <p>Cargando imágenes...</p>} {/* Mensaje de carga */}
    
        <div className="img-more"> {/* Añadir key aquí */}
          <div className="animate__animated animate__bounceIn">
            <h3>Imagen Binarizada</h3>
            <img src={`http://localhost:5000/${dataImages?.binary_image}`} alt="Imagen Binarizada" />
          </div>
          <div className="animate__animated animate__bounceIn">
            <h3>Imagen en Escala de Grises</h3>
            <img src={`http://localhost:5000/${dataImages?.gray_image}`} alt="Imagen en Escala de Grises" />
          </div>
          <div className="animate__animated animate__bounceIn">
            <h3>Imagen después de Apertura</h3>
            <img src={`http://localhost:5000/${dataImages?.opened_image}`} alt="Imagen después de Apertura" />
          </div>
          <div className="animate__animated animate__bounceIn">
            <h3>Imagen después de Cierre</h3>
            <img src={`http://localhost:5000/${dataImages?.closed_image}`} alt="Imagen después de Cierre" />
          </div>
          <div className="animate__animated animate__bounceIn">
            <h3>Imagen Compuesta de Quadbits</h3>
            <img src={`http://localhost:5000/${dataImages?.compound_image}`} alt="Imagen Compuesta de Quadbits" />
          </div>
          <div className="animate__animated animate__bounceIn">
            <h3>Imagen Etiquetada</h3>
            <img src={`http://localhost:5000/${dataImages?.processed_image}`} alt="Imagen Etiquetada" />
          </div>
          <div className="animate__animated animate__bounceIn">
            <h1>Número de Objetos: {dataImages?.num_objects}</h1> {/* Corregido el uso de ${} */}
          </div>
        </div>
      
    </>
  );
};

export default NewImages;

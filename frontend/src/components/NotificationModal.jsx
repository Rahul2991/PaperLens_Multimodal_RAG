import { ModalOverlay, ModalContainer, ModalHeader, Separator, ModalMessage, ModalButton } from '../components/StyleComponents';

/**
 * Notification Modal Component for displaying messages
 * Supports both success and error messages
 */
const NotificationModal = ({ message, type, onConfirm }) => {
    if (!message) return null;
    return (
        <ModalOverlay>
            <ModalContainer type={type}>
                <ModalHeader type={type}>{type === "success" ? "Success" : "Error"}</ModalHeader>
                <Separator />
                <ModalMessage>{message}</ModalMessage>
                <Separator />
                <ModalButton onClick={onConfirm}>OK</ModalButton>
            </ModalContainer>
        </ModalOverlay>
    );
};

export default NotificationModal;